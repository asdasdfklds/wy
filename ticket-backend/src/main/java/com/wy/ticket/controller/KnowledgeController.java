package com.wy.ticket.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.wy.ticket.common.Result;
import com.wy.ticket.dto.KnowledgeAddRequest;
import com.wy.ticket.entity.Knowledge;
import com.wy.ticket.service.KnowledgeService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;



@RestController 
@RequestMapping ("/knowledge")
public class KnowledgeController {

    @Autowired 
    private KnowledgeService knowledgeService;
    
    @PostMapping
    public Result<Knowledge> addKnowledge(@RequestBody KnowledgeAddRequest request) {
        return knowledgeService.addKnowledge(request);
    }

    @GetMapping
    public Result<List<Knowledge>> getKnowledgeList(){
        return knowledgeService.getKonwledgelist();
    }
    
}
