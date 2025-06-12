# Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import Any, Container, Dict, List, Optional, Pattern, Set, Sized, Tuple, Union

def chk_none(name : str, value : Any, reason=None) -> Any:
    if value is None: return value
    if reason is None: reason = 'must be None.'
    raise ValueError('{}({}) {}'.format(str(name), str(value), str(reason)))

def chk_not_none(name : str, value : Any, reason=None) -> Any:
    if value is not None: return value
    if reason is None: reason = 'must not be None.'
    raise ValueError('{}({}) {}'.format(str(name), str(value), str(reason)))

def chk_attribute(name : str, container : Dict, container_name : str, **kwargs):
    if name in container: return container[name]
    if 'default' in kwargs: return kwargs['default']
    raise AttributeError('Missing object({:s}) in container({:s})'.format(str(name), str(container_name)))

def chk_type(name : str, value : Any, type_or_types : Union[type, Set[type], Tuple[type]] = set()) -> Any:
    if isinstance(value, type_or_types): return value
    msg = '{}({}) is of a wrong type({}). Accepted type_or_types({}).'
    raise TypeError(msg.format(str(name), str(value), type(value).__name__, str(type_or_types)))

def chk_issubclass(name : str, value : type, class_or_classes : Union[type, Set[type]] = set()) -> Any:
    if issubclass(value, class_or_classes): return value
    msg = '{}({}) is of a wrong class({}). Accepted class_or_classes({}).'
    raise TypeError(msg.format(str(name), str(value), type(value).__name__, str(class_or_classes)))

def chk_length(
    name : str, value : Sized, allow_empty : bool = False,
    min_length : Optional[int] = None, max_length : Optional[int] = None) -> Any:

    length = len(chk_type(name, value, Sized))

    allow_empty = chk_type('allow_empty for {}'.format(name), allow_empty, bool)
    if not allow_empty and length == 0:
        raise ValueError('{}({}) is out of range: allow_empty({}).'.format(str(name), str(value), str(allow_empty)))

    if min_length is not None:
        min_length = chk_type('min_length for {}'.format(name), min_length, int)
        if length < min_length:
            raise ValueError('{}({}) is out of range: min_length({}).'.format(str(name), str(value), str(min_length)))

    if max_length is not None:
        max_length = chk_type('max_length for {}'.format(name), max_length, int)
        if length > max_length:
            raise ValueError('{}({}) is out of range: max_value({}).'.format(str(name), str(value), str(max_length)))

    return value

def chk_boolean(name : str, value : Any) -> bool:
    return chk_type(name, value, bool)

def chk_string(
    name : str, value : Any, allow_empty : bool = False,
    min_length : Optional[int] = None, max_length : Optional[int] = None,
    pattern : Optional[Union[Pattern, str]] = None) -> str:

    chk_type(name, value, str)
    chk_length(name, value, allow_empty=allow_empty, min_length=min_length, max_length=max_length)
    if pattern is None: return value
    pattern = re.compile(pattern)
    if pattern.match(value): return value
    raise ValueError('{}({}) does not match pattern({}).'.format(str(name), str(value), str(pattern)))

def chk_float(
    name : str, value : Any, type_or_types : Union[type, Set[type], List[type], Tuple[type]] = (int, float),
    min_value : Optional[Union[int, float]] = None, max_value : Optional[Union[int, float]] = None) -> float:

    chk_not_none(name, value)
    chk_type(name, value, type_or_types)
    if min_value is not None:
        chk_type(name, value, type_or_types)
        if value < min_value:
            msg = '{}({}) lower than min_value({}).'
            raise ValueError(msg.format(str(name), str(value), str(min_value)))
    if max_value is not None:
        chk_type(name, value, type_or_types)
        if value > max_value:
            msg = '{}({}) greater than max_value({}).'
            raise ValueError(msg.format(str(name), str(value), str(max_value)))
    return float(value)

def chk_integer(
    name : str, value : Any,
    min_value : Optional[Union[int, float]] = None, max_value : Optional[Union[int, float]] = None) -> int:

    return int(chk_float(name, value, type_or_types=int, min_value=min_value, max_value=max_value))

def chk_options(name : str, value : Any, options : Container) -> Any:
    chk_not_none(name, value)
    if value not in options:
        msg = '{}({}) is not one of options({}).'
        raise ValueError(msg.format(str(name), str(value), str(options)))
    return value
