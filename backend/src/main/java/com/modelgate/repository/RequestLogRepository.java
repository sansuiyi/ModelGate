package com.modelgate.repository;

import com.modelgate.entity.RequestLogEntity;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RequestLogRepository extends JpaRepository<RequestLogEntity, Long> {

    List<RequestLogEntity> findAllByOrderByTimestampDesc(Pageable pageable);

    List<RequestLogEntity> findByCustomerIdOrderByTimestampDesc(String customerId, Pageable pageable);

    List<RequestLogEntity> findAllByOrderByTimestampDesc();

    List<RequestLogEntity> findByCustomerId(String customerId);
}
