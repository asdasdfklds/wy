package com.wy.ticket.dto;


import com.wy.ticket.entity.User;
import lombok.Data;


@Data
public class LoginResponse {

    private Long id;
    private String username;
    private String realName;
    private String role;
    private String token;

    public static LoginResponse form(User user, String token) {
        LoginResponse loginResponse = new LoginResponse();
        loginResponse.id = user.getId();
        loginResponse.username = user.getUsername();
        loginResponse.realName = user.getRealName();
        loginResponse.role = user.getRole();
        loginResponse.token = token;
        return loginResponse;
    }

}
