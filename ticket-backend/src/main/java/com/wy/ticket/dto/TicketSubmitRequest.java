package com.wy.ticket.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 提交工单请求 DTO
 */
@Data
public class TicketSubmitRequest {

    @NotBlank(message = "标题不能为空")
    @Size(max = 200)
    private String title;

    @NotBlank(message = "描述不能为空")
    private String description;

    /** 故障类型：network / hardware / software / account，可选 */
    private String faultType;
}
