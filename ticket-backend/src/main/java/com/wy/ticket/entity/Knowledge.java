package com.wy.ticket.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 知识库实体
 *
 * 教学要点：
 * 原始文本存 MySQL，向量存 Milvus。Milvus 那边只存向量 + 知识 ID，
 * 检索时先拿 ID 回查 MySQL 取原始文本。
 */
@Data
@TableName("t_knowledge")
public class Knowledge {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String title;
    private String content;
    private String category;
    private Long creatorId;

    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
