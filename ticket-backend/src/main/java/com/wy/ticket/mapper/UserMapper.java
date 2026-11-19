package com.wy.ticket.mapper;

import org.apache.ibatis.annotations.Mapper;
import com.wy.ticket.entity.User;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

@Mapper 
public interface UserMapper extends BaseMapper<User> {

}
