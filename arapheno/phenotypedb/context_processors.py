from django.conf import settings

from . import __version__, __date__, __githash__,__build__, __buildurl__


def version(request):
    """Context processors for adding version and git information to all contexts"""
    BUILD_STATUS_URL = None
    if __buildurl__ != 'N/A':
        BUILD_STATUS_URL = __buildurl__

    version = {
        'githash':__githash__,
        'build':__build__,
        'version':__version__,
        'date':__date__,
        'build_status_url': BUILD_STATUS_URL,
        'github_url': settings.GITHUB_URL,
    }

    return {'version': version}