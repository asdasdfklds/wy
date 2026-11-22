package com.wy.ticket.service;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.wy.ticket.client.AgentClient;
import com.wy.ticket.common.Result;
import com.wy.ticket.dto.KnowledgeAddRequest;
import com.wy.ticket.entity.Knowledge;
import com.wy.ticket.mapper.KnowledgeMapper;

import cn.dev33.satoken.stp.StpUtil;
import lombok.extern.slf4j.Slf4j;

@Slf4j 
@Service 
public class KnowledgeService {

    @Autowired 
    private KnowledgeMapper knowledgeMapper;

    @Autowired 
    private AgentClient agentClient;

    public Result<Knowledge> addKnowledge(KnowledgeAddRequest request) {
        Knowledge knowledge = new Knowledge();
        knowledge.setTitle(request.getTitle());
        knowledge.setContent(request.getContent());
        knowledge.setCreatorId(StpUtil.getLoginIdAsLong());
        knowledge.setCategory(request.getCategory());
        knowledge.setCreateTime(LocalDateTime.now());
        knowledge.setUpdateTime(LocalDateTime.now());
        knowledgeMapper.insert(knowledge);

        //调用aiagent服务，将知识库存储在向量数据库milvus
        boolean ok = agentClient.addKnowledge(request);
        log.info("知识库{}同步到Agent{}",knowledge.getId(),ok?"成功":"失败");
        return Result.success(knowledge);
    }

    public Result<List<Knowledge>> getKonwledgelist(){
        List<Knowledge> knowledgeList = knowledgeMapper.selectList(Wrappers.lambdaQuery(Knowledge.class));
        return Result.success(knowledgeList);

    }


}
