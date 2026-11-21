package com.wy.ticket.mapper;

import org.apache.ibatis.annotations.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.wy.ticket.entity.Ticket;


@Mapper 
public interface TicketMapper extends BaseMapper<Ticket> {

}
