package com.wy.ticket.config;

import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import cn.dev33.satoken.context.SaHolder;
import cn.dev33.satoken.exception.NotLoginException;
import cn.dev33.satoken.interceptor.SaInterceptor;
import cn.dev33.satoken.stp.StpUtil;

public class SaTokenConfig implements WebMvcConfigurer{


    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new SaInterceptor(handle->{
            String token = SaHolder.getRequest().getHeader(StpUtil.getTokenName());
            if(token == null){
                throw new NotLoginException("未登录", NotLoginException.NOT_TOKEN,NotLoginException.NOT_TOKEN);
            }
            Object id = StpUtil.getLoginIdByToken(token);
            if(id == null){
                throw new NotLoginException("无效token", NotLoginException.NOT_TOKEN,NotLoginException.NOT_TOKEN);
            }
        })).addPathPatterns("/**");
    }
}
