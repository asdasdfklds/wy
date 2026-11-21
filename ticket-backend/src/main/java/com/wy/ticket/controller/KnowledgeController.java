package com.wy.ticket.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wy.ticket.common.Result;
import com.wy.ticket.dto.KnowledgeAddRequest;
import com.wy.ticket.entity.Knowledge;
import com.wy.ticket.service.KnowledgeService;
import org.springframework.web.bind.annotation.PostMapping;


@RestController 
@RequestMapping ("/knowledge")
public class KnowledgeController {

    @Autowired 
    private KnowledgeService knowledgeService;
    
    @PostMapping
    public Result<Knowledge> addKnowledge(@RequestBody KnowledgeAddRequest request) {
        return knowledgeService.addKnowledge(request);
    }

}
