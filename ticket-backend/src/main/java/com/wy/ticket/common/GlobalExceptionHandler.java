package com.wy.ticket.common;

import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import cn.dev33.satoken.exception.NotLoginException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(value = IllegalArgumentException.class)
    public Result<Void> handleIllegal(IllegalArgumentException e) {
        return Result.error(400, e.getMessage());
    }

    @ExceptionHandler(value = NotLoginException.class)
    public Result<Void> handleNotLoginException(NotLoginException e) {
        e.printStackTrace();
        return Result.error(400, e.getMessage());
    }

    @ExceptionHandler(value = Exception.class)
    public Result<Void> handleException(Exception e) {
        e.printStackTrace();
        return Result.error("服务器内部异常:" + e.getMessage());
    }
}
