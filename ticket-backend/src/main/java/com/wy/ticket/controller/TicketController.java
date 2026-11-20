package com.wy.ticket.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import com.wy.ticket.common.PageData;
import com.wy.ticket.common.Result;
import com.wy.ticket.entity.Ticket;
import com.wy.ticket.service.TicketService;

@Controller 
@RequestMapping ("/ticket")
public class TicketController {

    @Autowired
    private TicketService ticketService;

    @GetMapping
    public Result<PageData<Ticket>> getTicket(Integer page, Integer size, String status, String dateFrom, String dateTo) {
        return Result.success(ticketService.getPageData(page, size, status, dateFrom, dateTo));
    }
}
