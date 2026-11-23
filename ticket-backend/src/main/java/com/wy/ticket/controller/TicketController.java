package com.wy.ticket.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wy.ticket.common.PageData;
import com.wy.ticket.common.Result;
import com.wy.ticket.dto.TicketSubmitRequest;
import com.wy.ticket.dto.TicketUpdateRequest;
import com.wy.ticket.entity.Ticket;
import com.wy.ticket.service.TicketService;

@RestController 
@RequestMapping ("/ticket")
public class TicketController {

    @Autowired
    private TicketService ticketService;

    @GetMapping
    public Result<PageData<Ticket>> getTicket(Integer page, Integer size, String status, String dateFrom, String dateTo) {
        return Result.success(ticketService.getPageData(page, size, status, dateFrom, dateTo));
    }

    @GetMapping("/{id}")
    public Result<Ticket> getTicketDetail(@PathVariable Long id) {
        Ticket ticket = ticketService.getTicketDetail(id);
        return Result.success(ticket);
    }

    @PostMapping
    public Result<Ticket> submit(@RequestBody TicketSubmitRequest request) {
        return Result.success(ticketService.submit(request));
    }

    @PutMapping("/{id}")
    public Result<Ticket> update(@PathVariable Long id, @RequestBody TicketUpdateRequest request) {
        return ticketService.updateTicket(id, request);
    }
}
