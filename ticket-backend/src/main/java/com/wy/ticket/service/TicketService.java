package com.wy.ticket.service;


import cn.dev33.satoken.stp.StpUtil;
import com.alibaba.fastjson2.JSON;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.wy.ticket.client.AgentClient;
import com.wy.ticket.common.PageData;
import com.wy.ticket.common.Result;
import com.wy.ticket.dto.AIAnalyzeResponse;
import com.wy.ticket.dto.TicketSubmitRequest;
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

    @Autowired
    private AgentClient agentClient;

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
        //new Page<>(page, size)指定是第几个总条数。 表示分页参数，page 是当前页码，size 是每页显示的记录数
        //queryWrapper 是查询条件，selectPage 方法会根据这些条件查询数据库，并返回一个 Page 对象，里面包含了查询结果和分页信息。
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

    public Ticket submit(TicketSubmitRequest request) {
        Ticket ticket = new Ticket();
        ticket.setTitle(request.getTitle());
        ticket.setDescription(request.getDescription());
        ticket.setFaultType(request.getFaultType());
        ticket.setStatus("PENDING");
        ticket.setSubmitterId(StpUtil.getLoginIdAsLong());
        ticket.setCreateTime(LocalDateTime.now());
        ticket.setUpdateTime(LocalDateTime.now());
        ticketMapper.insert(ticket);
          //调用AI agent
        Object result = agentClient.analyzeTicket(ticket);
        AIAnalyzeResponse response = JSON.parseObject(JSON.toJSONString(result), AIAnalyzeResponse.class);
        ticket.setSimilarTickets(response.getSimilarTickets());
        ticket.setSimilarKnowledge(response.getSimilarKnowledge());
        ticket.setFaultType(response.getFaultType());
        ticket.setAiSuggestion(response.getSuggestion());
        ticketMapper.updateById(ticket);

        return ticket;
    }

}
