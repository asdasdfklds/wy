package com.wy.ticket.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.wy.ticket.dto.LoginRequest;
import com.wy.ticket.entity.User;
import com.wy.ticket.mapper.UserMapper;
import cn.dev33.satoken.stp.StpUtil;



@Service 
public class UserService {

   @Autowired
   private UserMapper userMapper;

    public User login(LoginRequest loginRequest) {
        User user = userMapper.selectOne(Wrappers.lambdaQuery(User.class).eq(User::getUsername, loginRequest.getUsername()));
        if (user == null) {
           return null;
        }
        if (!user.getPassword().equals(loginRequest.getPassword())) {
            return user;
        }
        return null;
    }   
}



