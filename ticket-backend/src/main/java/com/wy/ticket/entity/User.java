package com.wy.ticket.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.IdType;
import java.time.LocalDateTime;

import lombok.Data;

@Data 
@TableName ("t_user")
public class User {
    @TableId (type = IdType.AUTO)
    private Long id;

    private String username;

    private String password;

    private String realName;

    private String role;

    private LocalDateTime createTime;
}
