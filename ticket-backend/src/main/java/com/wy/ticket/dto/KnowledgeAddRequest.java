package com.wy.ticket.dto;


import lombok.Data;

/*
 * @Author Kevin
 * @Description
 **/
@Data
public class KnowledgeAddRequest {

    private Long id;
    private String title;
    private String content;
    private String category;

}
