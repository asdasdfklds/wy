package com.wy.ticket.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.wy.ticket.dto.LoginRequest;
import com.wy.ticket.dto.LoginResponse;
import com.wy.ticket.entity.User;
import com.wy.ticket.mapper.UserMapper;
import cn.dev33.satoken.stp.StpUtil;



@Service 
public class UserService {

   @Autowired
   private UserMapper userMapper;

    public LoginResponse login(LoginRequest loginRequest) {
        User user = userMapper.selectOne(Wrappers.lambdaQuery(User.class).eq(User::getUsername, loginRequest.getUsername()));
        if (user == null) {
           throw new IllegalArgumentException("用户名不存在");
        }
        if (!user.getPassword().equals(loginRequest.getPassword())) {
            throw new IllegalArgumentException("密码错误");
        }
        StpUtil.login(user.getId());
        String token = StpUtil.getTokenValue();
        return LoginResponse.form(user, token);
    }   
}



