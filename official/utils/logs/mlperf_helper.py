# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Wrapper for the mlperf logging utils.

MLPerf compliance logging is only desired under a limited set of circumstances.
This module is intended to keep users from needing to consider logging (or
install the module) unless they are performing mlperf runs.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

_MIN_VERSION = (0, 0, 4)
_STACK_OFFSET = 2


def get_mlperf_log():
  try:
    import pkg_resources
    import mlperf_compliance

    _version = pkg_resources.get_distribution("mlperf_compliance")
    _version = tuple(int(i) for i in _version.version.split("."))
    if _version < _MIN_VERSION:
      tf.logging.warning(
          "mlperf_compliance is version {}, must be at least version {}".format(
              ".".join([str(i) for i in VERSION]),
              ".".join([str(i) for i in _MIN_VERSION])))
      raise ImportError

    mlperf_log = mlperf_compliance.mlperf_log

  except ImportError:
    mlperf_log = None

  return mlperf_log


class Logger(object):
  class Tags(object):
    def __init__(self, mlperf_log):
      self.enabled = False
      self.mlperf_log = mlperf_log

    def __getattr__(self, item):
      if self.mlperf_log is None:
        return
      return getattr(self.mlperf_log, item)

  def __init__(self):
    self._enabled = False
    self._mlperf_log = get_mlperf_log()
    self.tags = self.Tags(self._mlperf_log)

  def __call__(self, enable=False):
    self._enabled = enable
    self.tags.enabled = enable
    return self

  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc_val, exc_tb):
    self._enabled = False
    self.tags.enabled = False

  @property
  def enabled(self):
    return self._enabled

  def ncf_print(self,key, value=None, stack_offset=_STACK_OFFSET,
                deferred=False, extra_print=False):
    if self._mlperf_log is None:
      return
    self._mlperf_log.ncf_print(key=key, value=value, stack_offset=stack_offset,
                               deferred=deferred, extra_print=extra_print)


LOGGER = Logger()


if __name__ == "__main__":
  with LOGGER(True):
    LOGGER.ncf_print(key=LOGGER.tags.RUN_START)
    LOGGER.ncf_print(key=LOGGER.tags.RUN_STOP)
