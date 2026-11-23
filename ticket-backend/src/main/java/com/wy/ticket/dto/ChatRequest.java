package com.wy.ticket.dto;


import lombok.Data;

/*
 * @Author Kevin
 * @Description
 **/
@Data
public class ChatRequest {
    private String sessionId;
    private String message;
}
