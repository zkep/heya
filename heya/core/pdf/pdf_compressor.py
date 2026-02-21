from __future__ import annotations

import logging
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from io import BytesIO
from typing import Any, Dict

from PIL import Image as PILImage
from pypdf import PdfReader, PdfWriter as PyPdfWriter
from heya.core.exceptions import CompressError
from heya.core.models import PdfContent
from heya.core.pdf.compression import compress_pdf
from heya.core.pdf.pypdf_writer import PdfWriter

# Set up logger
logger = logging.getLogger(__name__)

__all__ = ["PdfCompressor", "compress"]


class PdfCompressor:
    _COMPRESSION_LEVELS = {
        0: {"stream_level": 9, "compress_images": True},  
        1: {"stream_level": 6, "compress_images": True},  
        2: {"stream_level": 3, "compress_images": False}, 
    }

    def __init__(self, max_workers: int | None = None) -> None:
        # Dynamically determine thread pool size based on system resources
        if max_workers is None:
            # Get CPU count and available memory
            cpu_count = multiprocessing.cpu_count()
            
            # Use 1-2 times the number of CPU cores for CPU-bound tasks
            # but limit to a reasonable maximum to avoid overloading
            self._max_workers = min(cpu_count * 2, 8)  # Maximum 8 threads
        else:
            self._max_workers = max_workers
        
        # Performance statistics
        self._stats: Dict[str, Any] = {
            'total_compressions': 0,
            'total_time': 0.0,
            'total_size_reduction': 0,
            'avg_compression_ratio': 0.0,
        }
    
    def _get_optimal_thread_count(self, task_type: str, page_count: int = 1) -> int:
        """
        Get optimal thread count based on task type and page count
        
        Args:
            task_type: Type of task ('single' or 'batch')
            page_count: Number of pages to process
            
        Returns:
            Optimal thread count
        """
        cpu_count = multiprocessing.cpu_count()
        
        if task_type == 'batch':
            # For batch processing, use more conservative thread count
            # to leave resources for other processes
            return min(cpu_count, 4)
        else:
            # For single PDF processing, adjust based on page count
            if page_count <= 5:
                # Few pages, use fewer threads
                return min(cpu_count, 2)
            elif page_count <= 20:
                # Moderate pages, use moderate threads
                return min(cpu_count * 2, 6)
            else:
                # Many pages, use more threads but limit
                return min(cpu_count * 2, 8)
    
    def _compress_image(self, image_data: bytes) -> bytes | None:
        """
        Compress image data using PIL
        
        Args:
            image_data: Original image data
            
        Returns:
            Compressed image data or None if compression failed
        """
        try:
            # Open image using PIL
            with PILImage.open(BytesIO(image_data)) as img:
                # Convert to RGB if necessary
                if img.mode == 'RGBA':
                    # Create a white background
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    # Paste image with alpha channel
                    background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image if it's too large
                max_dimension = 1200  # Maximum width or height
                width, height = img.size
                
                if width > max_dimension or height > max_dimension:
                    # Calculate new size maintaining aspect ratio
                    if width > height:
                        new_width = max_dimension
                        new_height = int(height * (max_dimension / width))
                    else:
                        new_height = max_dimension
                        new_width = int(width * (max_dimension / height))
                    
                    img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                
                # Compress image with moderate quality
                output = BytesIO()
                img.save(output, format='JPEG', quality=75, optimize=True, progressive=True)
                compressed_data = output.getvalue()
                
                # Only return if compression actually reduced size
                if len(compressed_data) < len(image_data):
                    return compressed_data
                return None
        except Exception as e:
            # Log image compression error and return None
            logger.debug(f"Error compressing image: {e}")
            return None

    def compress(self, content: PdfContent, quality: int = 0) -> PdfContent:
        start_time = time.time()
        original_size = len(content.data)
        
        try:
            settings = self._COMPRESSION_LEVELS.get(
                quality, self._COMPRESSION_LEVELS[0]
            )

            reader = PdfReader(BytesIO(content.data))
            writer = PyPdfWriter()

            compressed_data = self._compress_pages_parallel(reader, writer, settings)
            compressed_size = len(compressed_data)

            if compressed_size >= original_size:
                logger.info(
                    f"PDF compression skipped: original={original_size/1024:.2f}KB, "
                    f"compressed={compressed_size/1024:.2f}KB, "
                    f"reduction={original_size-compressed_size/1024:.2f}KB, "
                    f"time={time.time() - start_time:.2f}s"
                )
                return content
            
            # Update performance statistics
            compression_time = time.time() - start_time
            size_reduction = original_size - compressed_size
            compression_ratio = (size_reduction / original_size * 100) if original_size > 0 else 0
            
            self._stats['total_compressions'] += 1
            self._stats['total_time'] += compression_time
            self._stats['total_size_reduction'] += size_reduction
            
            # Update average compression ratio
            if self._stats['total_compressions'] > 0:
                self._stats['avg_compression_ratio'] = (
                    self._stats['total_size_reduction'] / 
                    (self._stats['total_compressions'] * original_size) * 100
                )
            
            # Log compression results
            logger.info(
                f"PDF compression completed: original={original_size/1024:.2f}KB, "
                f"compressed={compressed_size/1024:.2f}KB, "
                f"reduction={size_reduction/1024:.2f}KB ({compression_ratio:.1f}%), "
                f"time={compression_time:.2f}s"
            )
            
            return PdfContent(compressed_data)

        except ImportError:
            raise CompressError(
                "pypdf is not installed. Install with: pip install pypdf"
            )
        except Exception as e:
            raise CompressError(f"PDF compression failed: {e}") from e

    def _compress_pages_parallel(
        self, reader: Any, writer: Any, settings: dict[str, Any]
    ) -> bytes:
        def process_page(page_data: tuple[int, Any]) -> tuple[int, Any] | None:
            page_idx, page = page_data
            try:
                # Execute compression in thread
                page.compress_content_streams(level=settings["stream_level"])
                
                # If image compression is enabled
                if settings.get("compress_images", False):
                    try:
                        for image in page.images:
                            try:
                                image_data = image.data
                                if len(image_data) > 1024:
                                    # Compress images larger than 1KB
                                    compressed_image_data = self._compress_image(image_data)
                                    if compressed_image_data and len(compressed_image_data) < len(image_data):
                                        # Update the image data if compression was successful
                                        image.update(compressed_image_data)
                            except Exception as e:
                                # Log image compression error, but continue processing other images
                                logger.debug(f"Error compressing image: {e}")
                    except Exception as e:
                        # Log page image access error, but continue processing page
                        logger.debug(f"Error accessing images on page {page_idx}: {e}")
                
                return (page_idx, page)
            except Exception as e:
                # Log page processing error, but continue processing other pages
                logger.debug(f"Error processing page {page_idx}: {e}")
                return None

        # Process pages in batches to reduce memory usage
        total_pages = len(reader.pages)
        
        # Dynamically adjust batch size based on page count
        if total_pages <= 10:
            batch_size = total_pages
        elif total_pages <= 50:
            batch_size = 10
        elif total_pages <= 100:
            batch_size = 15
        else:
            batch_size = 20
        
        processed_pages: list[tuple[int, Any]] = []
        
        # Get optimal thread count based on page count
        optimal_threads = self._get_optimal_thread_count('single', total_pages)

        for i in range(0, total_pages, batch_size):
            batch = list(enumerate(reader.pages[i:i+batch_size]))
            
            with ThreadPoolExecutor(max_workers=optimal_threads) as executor:
                future_to_page = {
                    executor.submit(process_page, page_data): page_data[0]
                    for page_data in batch
                }

                for future in as_completed(future_to_page):
                    result = future.result()
                    if result:
                        processed_pages.append(result)

        # Sort by page index
        processed_pages.sort(key=lambda x: x[0])
        
        # Add processed pages
        for page_idx, page in processed_pages:
            writer.add_page(page)

        # Ensure at least one page is processed
        if not processed_pages:
            # If all pages failed processing, add original pages
            for page in reader.pages:
                writer.add_page(page)

        # Use BytesIO for output, but optimize for large PDFs
        output = BytesIO()
        
        # Write in chunks if possible (depends on PyPDF2 implementation)
        writer.write(output)
        output.seek(0)
        
        # For very large PDFs, return the value directly to avoid keeping the buffer in memory
        return output.getvalue()

    def compress_batch(
        self, contents: list[PdfContent], quality: int = 0
    ) -> list[PdfContent]:
        batch_start_time = time.time()
        total_original_size = sum(len(content.data) for content in contents)
        
        # For batch processing, use process pool to better utilize multi-core CPU
        # Get optimal process pool size based on batch size
        process_pool_size = self._get_optimal_thread_count('batch')
        
        with ProcessPoolExecutor(max_workers=process_pool_size) as executor:
            futures = [
                executor.submit(self.compress, content, quality) for content in contents
            ]
            results = []
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    raise CompressError(f"Batch compression failed: {e}") from e
        
        batch_time = time.time() - batch_start_time
        total_compressed_size = sum(len(result.data) for result in results)
        total_batch_reduction = total_original_size - total_compressed_size
        batch_compression_ratio = (total_batch_reduction / total_original_size * 100) if total_original_size > 0 else 0
        
        # Log batch compression results
        logger.info(
            f"Batch compression completed: {len(contents)} PDFs, "
            f"original={total_original_size/1024:.2f}KB, "
            f"compressed={total_compressed_size/1024:.2f}KB, "
            f"reduction={total_batch_reduction/1024:.2f}KB ({batch_compression_ratio:.1f}%), "
            f"time={batch_time:.2f}s"
        )
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics
        
        Returns:
            Dictionary containing performance statistics
        """
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """
        Reset performance statistics
        """
        self._stats = {
            'total_compressions': 0,
            'total_time': 0.0,
            'total_size_reduction': 0,
            'avg_compression_ratio': 0.0,
        }


def compress(
    source: str | bytes,
    target: str,
    quality: int = 0,
) -> None:
    compressor = PdfCompressor()
    writer = PdfWriter()

    if isinstance(source, str):
        with open(source, "rb") as f:
            content = PdfContent(f.read())
    else:
        content = PdfContent(source)

    compressed = compress_pdf(content, quality, compressor.compress)
    writer.write(compressed, target)
