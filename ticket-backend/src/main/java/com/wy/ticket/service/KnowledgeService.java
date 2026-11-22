package com.wy.ticket.service;


import cn.dev33.satoken.stp.StpUtil;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.wy.ticket.client.AgentClient;
import com.wy.ticket.common.Result;
import com.wy.ticket.dto.KnowledgeAddRequest;
import com.wy.ticket.entity.Knowledge;
import com.wy.ticket.mapper.KnowledgeMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/*
 * @Author Kevin
 * @Description
 **/
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
        request.setId(knowledge.getId());
        //调用AI agent 服务，将知识库存储在向量数据库milvus
        boolean ok = agentClient.addKnowledge(request);
        log.info("知识库{} 同步到 Agent {}", knowledge.getId(), ok ? "成功" : "失败");
        return Result.success(knowledge);
    }


    public Result<List<Knowledge>> getKnowledgeList(){
       List<Knowledge> knowledgeList = knowledgeMapper.selectList(Wrappers.lambdaQuery(Knowledge.class));
       return Result.success(knowledgeList);
    }

    public Result<Void> deleteKnowledge(long id) {
        knowledgeMapper.deleteById(id);
        agentClient.deleteKnowledge(id);
        return Result.success();
    }

}
