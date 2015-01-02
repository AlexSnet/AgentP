import platform

from agentp.platforms.linux import Linux


Platform = locals()[platform.system()]()

__all__ = [Platform]
