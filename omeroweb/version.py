try:
    from omero_version import omero_version
    from omero_version import build_year as omero_buildyear
except ImportError as ie:
    # Especially common during setup.py
    omero_version = "unknown"
    omero_buildyear = "unknown"


omeroweb_version = "5.5.dev2"
omeroweb_buildyear = "2019"
