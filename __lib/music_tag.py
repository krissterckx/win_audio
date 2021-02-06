import music_tag   # pip install music-tag

# -------------------------------------------------------------------------
#                           ===============
#                           About music-tag
#                           ===============
#
#
# /usr/lib/python2.7/site-packages/music_tag/file.py
# .local/lib/python3.8/site-packages/music_tag/file.py
#
# ( Windows:
#   "C:\Users\$USER\AppData\Local\Programs\Python\Python39\lib\
#      site-packages\music_tag\file.py" )
#
#
#               --------------- CHANGE 1 ---------------
# Add:
#
# import sys
# def u(x):
#     if sys.version_info < (3, 0):
#         return unicode(x)
#     return str(x)
#
# and replace all str(x) occurrences by u(x)
#
#
#               --------------- CHANGE 2 ---------------
# Change:
#
#  def values(self, val):
#      if isinstance(val, (list, tuple)):
#          self._values = list(val)
#      elif val is None:
#          self._values = []
#      else:
#          self._values = [val]
#      for i, v in enumerate(self._values):
#          if self.sanitizer is not None:
#              v = self.sanitizer(v)
#          # if not (self.type is None or ...)):  # <<< TODO(REMOVE)
#          #     v = self.type(v)  # <<< TODO(REMOVE)
#          self._values[i] = u(v)  # <<< TODO(ADD u())
#
#
# -------------------------------------------------------------------------


def m_load_file(p):
    return music_tag.load_file(p)
