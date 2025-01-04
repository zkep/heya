import sys

__all__ = ("main",)


def main() -> None:
    from heya.bin.heya import main as _main

    sys.exit(_main())


if __name__ == "__main__":  # pragma: no cover
    main()
