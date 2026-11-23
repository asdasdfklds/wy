package com.wy.ticket.controller;


import com.wy.ticket.common.Result;
import com.wy.ticket.dto.ChatRequest;
import com.wy.ticket.dto.ChatResponse;
import com.wy.ticket.service.ChatService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/*
 * @Author Kevin
 * @Description
 **/
@RestController
@RequestMapping("/chat")
public class ChatController {

    @Autowired
    private ChatService chatService;

    @PostMapping
    public Result<ChatResponse> chat(@RequestBody ChatRequest chatRequest) {
        return chatService.chat(chatRequest);
    }

}
