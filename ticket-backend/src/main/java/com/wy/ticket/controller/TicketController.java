package com.wy.ticket.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.wy.ticket.common.Result;

@Controller 
@RequestMapping ("/ticket")
public class TicketController {

    @RequestMapping("/getTicket")
    public Result<String> getTicket(){
    return Result.success("ticket");
    }
}
