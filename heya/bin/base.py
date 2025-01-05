from __future__ import annotations

import click
from collections import OrderedDict


class HeyaOption(click.Option):
    """Customized option for Heya."""

    def get_default(self, ctx, *args, **kwargs):
        if self.default_value_from_context:
            self.default = ctx.obj[self.default_value_from_context]
        return super().get_default(ctx, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        """Initialize a Heya option."""
        self.help_group = kwargs.pop("help_group", None)
        self.default_value_from_context = kwargs.pop("default_value_from_context", None)
        super().__init__(*args, **kwargs)


class HeyaCommand(click.Command):
    """Customized command for Heya."""

    def format_options(self, ctx, formatter):
        """Write all the options into the formatter if they exist."""
        opts = OrderedDict()
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                if hasattr(param, "help_group") and param.help_group:
                    opts.setdefault(str(param.help_group), []).append(rv)
                else:
                    opts.setdefault("Options", []).append(rv)

        for name, opts_group in opts.items():
            with formatter.section(name):
                formatter.write_dl(opts_group)
