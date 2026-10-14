package com.modelgate.repository;

import com.modelgate.entity.CustomerEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CustomerRepository extends JpaRepository<CustomerEntity, String> {

    List<CustomerEntity> findAllByOrderByCreatedAtDesc();
}
