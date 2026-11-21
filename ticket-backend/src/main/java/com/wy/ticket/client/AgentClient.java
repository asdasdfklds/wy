package com.wy.ticket.client;

import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import com.wy.ticket.entity.Ticket;

import org.springframework.beans.factory.annotation.Value;

@Component 
public class AgentClient {

    @Value ("${agent.base-url}")
    private String baseUrl;

    RestTemplate restTemplate = new RestTemplate();
    //调用ai agent分析工单
    public Object analyzeTicket(Ticket ticket) {
        Object result = restTemplate.postForEntity(baseUrl + "/analyze", ticket, Object.class).getBody();

        return result;
    }

}
