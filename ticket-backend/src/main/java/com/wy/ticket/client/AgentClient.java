package com.wy.ticket.client;


import com.wy.ticket.dto.KnowledgeAddRequest;
import com.wy.ticket.entity.Ticket;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;


/*
 * @Author Kevin
 * @Description
 **/
@Component
public class AgentClient {

    @Value("${agent.base-url}")
    private String baseUrl;

    RestTemplate restTemplate = new RestTemplate();

    /**
     * 调用AI agent服务分析工单
     *
     * @param ticket
     * @return
     */
    public Object analyzeTicket(Ticket ticket) {
        Object result = restTemplate.postForEntity(baseUrl + "/analyze", ticket, Object.class).getBody();

        return result;
    }

    public Boolean addKnowledge(KnowledgeAddRequest request) {
        ResponseEntity<Boolean> result = restTemplate.postForEntity(baseUrl + "/knowledge/add", request, Boolean.class);
        return result.getBody();
    }

    public Boolean deleteKnowledge(Long id) {
        restTemplate.delete(baseUrl + "/knowledge/" + id);
        return true;
    }



    public Boolean updateTicket(Ticket ticket) {
        Map<String, Object> param = new HashMap<>();
        param.put("item_id", ticket.getId());
        param.put("title", ticket.getTitle());
        param.put("description", ticket.getDescription());
        param.put("resolution", ticket.getResolution());
        param.put("fault_type", ticket.getFaultType());
        ResponseEntity<Boolean> result = restTemplate.postForEntity(baseUrl + "/ticket", param, Boolean.class);
        return result.getBody();
    }
}
