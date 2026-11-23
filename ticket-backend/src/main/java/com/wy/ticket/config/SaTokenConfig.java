package com.wy.ticket.config;

import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import cn.dev33.satoken.context.SaHolder;
import cn.dev33.satoken.exception.NotLoginException;
import cn.dev33.satoken.interceptor.SaInterceptor;
import cn.dev33.satoken.stp.StpUtil;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SaTokenConfig implements WebMvcConfigurer{

    @Value ("${agent.token}")
    private String agentToken;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new SaInterceptor(handler->{
            String token = SaHolder.getRequest().getHeader(StpUtil.getTokenName());
            if(token==null){
                throw new NotLoginException("未登录",NotLoginException.NOT_TOKEN,NotLoginException.NOT_TOKEN);
            }
            if(agentToken.equals(token)){
                StpUtil.login(3);
                return;
            }
            if (token.startsWith("Bearer ")) {
               token = token.substring(7,token.length());
            }
            Object id = StpUtil.getLoginIdByToken(token);
            if(id==null){
                throw new NotLoginException("无效token",NotLoginException.INVALID_TOKEN,NotLoginException.INVALID_TOKEN);
            }
        })).addPathPatterns("/**");
    }

}
