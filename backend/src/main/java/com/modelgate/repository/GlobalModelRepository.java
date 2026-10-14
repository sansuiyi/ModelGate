package com.modelgate.repository;

import com.modelgate.entity.GlobalModelEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface GlobalModelRepository extends JpaRepository<GlobalModelEntity, String> {

    List<GlobalModelEntity> findByEnabled(int enabled);
}
