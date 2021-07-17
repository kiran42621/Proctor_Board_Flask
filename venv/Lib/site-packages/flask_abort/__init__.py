from contextlib import contextmanager
from enum import Enum

from flask import abort


class HTTPCode(Enum):
    # 1、语义有误，当前请求无法被服务器理解。除非进行修改，否则客户端不应该重复提交这个请求。
    # 2、请求参数有误。
    bad_request = 400
    # 未授权
    unauthorized = 401
    # 服务器已经理解请求，但是拒绝执行它
    forbidden = 403
    # 404
    not_found = 404
    # 500
    system_error = 500


@contextmanager
def wrap_abort(code: int, logger):
    """
    usage:

    from functools import partial
    wrap_abort = partial(wrap_abort, logger=logger)

    # api interface response http code is 500 when throw exception
    with wrap_abort(500):
        raise Exception('this is exception')

    # add these code to escape to be handled if having flask.errorhandler

    from werkzeug.exceptions import HTTPException
    @app.errorhandler(Exception)
    def handle_flask_error(e):
        if isinstance(e, HTTPException):
            return e

    :param code: int, http code
    :param logger:
    :return: None
    """
    try:
        yield
    except Exception as e:
        if code >= HTTPCode.system_error.value:
            logger.exception(e)
        else:
            logger.info(e)
        return abort(code)
