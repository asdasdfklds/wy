package com.wy.ticket.common;

import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler (value = IllegalArgumentException.class)
    public Result<Void> handle (IllegalArgumentException e){
        return Result.error(400, e.getMessage());
    }

    @ExceptionHandler (value = Exception.class)
    public Result<Void> handleExeception (Exception e){
        return Result.error(e.getMessage());
    }

}
