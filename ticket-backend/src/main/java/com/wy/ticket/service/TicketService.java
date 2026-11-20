package com.wy.ticket.service;


import cn.dev33.satoken.stp.StpUtil;
import com.alibaba.fastjson2.JSON;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.wy.ticket.common.PageData;
import com.wy.ticket.common.Result;
import com.wy.ticket.entity.Ticket;
import com.wy.ticket.mapper.TicketMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;


@Slf4j
@Service
public class TicketService {

    @Autowired
    private TicketMapper ticketMapper;

    public PageData<Ticket> getPageData(int page, int size, String status, String dateFrom, String dateTo) {
        QueryWrapper<Ticket> queryWrapper = new QueryWrapper<Ticket>();
        if (status != null && !status.equals("")) {
            queryWrapper.eq("status", status);
        }
        if (dateFrom != null && !dateFrom.equals("")) {
            queryWrapper.ge("create_date", dateFrom + " 00:00:00");
        }
        if (dateTo != null && !dateTo.equals("")) {
            queryWrapper.le("create_date", dateTo + " 23:59:59");
        }
        Page<Ticket> ticketPage = ticketMapper.selectPage(new Page<>(page, size), queryWrapper);
        PageData<Ticket> pageData = new PageData<>();
        pageData.setTotal(ticketPage.getTotal());
        pageData.setList(ticketPage.getRecords());
        return pageData;
    }


    public Ticket getTicketDetail(Long ticketId) {
        Ticket ticket = ticketMapper.selectById(ticketId);
        return ticket;
    }

}
