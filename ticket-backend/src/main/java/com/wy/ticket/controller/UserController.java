package com.wy.ticket.controller;

import org.springframework.web.bind.annotation.RestController;

import com.wy.ticket.dto.LoginRequest;
import com.wy.ticket.entity.User;

import jakarta.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import com.wy.ticket.service.UserService;

@RestController 
@RequestMapping ("/user")
public class UserController {
    
    @Autowired 
    private UserService userService;

    @RequestMapping ("/login")
    public User login( @RequestBody @Valid LoginRequest loginRequest) {
        return userService.login(loginRequest);
    }
}