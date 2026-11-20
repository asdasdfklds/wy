package com.wy.ticket.common;

import lombok.Data;

import java.util.List;

/*
 * @Author Kevin
 * @Description 
 **/
@Data
public class PageData<T> {

  private Long total;
  private List<T> list;
}
