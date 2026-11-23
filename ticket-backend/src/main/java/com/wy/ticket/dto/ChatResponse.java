package com.wy.ticket.dto;


import com.alibaba.fastjson2.annotation.JSONField;
import lombok.Data;

import java.util.List;
import java.util.Map;

/*
 * @Author Kevin
 * @Description
 **/
@Data
public class ChatResponse {

    private String reply;
    @JSONField(name = "tool_calls")
    private List<Map<String, Object>> toolCalls;

    @JSONField(name = "session_id")
    private String sessionId;

    private Boolean finished;
}
