package com.wy.ticket.entity;


import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/*
 * @Author Kevin
 * @Description
 **/
@Data
@TableName("t_ticket")
public class Ticket {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 标题 */
    private String title;

    /** 描述 */
    private String description;

    /** 故障类型：network/hardware/software/account */
    private String faultType;

    /** 状态：PENDING/PROCESSING/RESOLVED/CLOSED */
    private String status;

    /** 提交人 */
    private Long submitterId;

    /** 处理人 */
    private Long assigneeId;

    /** Agent 生成的初步建议（JSON） */
    private String aiSuggestion;

    /** 相似历史工单（JSON） */
    private String similarTickets;

    /** 知识库参考（JSON） */
    private String similarKnowledge;

    /** 最终处理结果 */
    private String resolution;

    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
