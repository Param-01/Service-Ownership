import {
  BeforeInsert,
  Column,
  CreateDateColumn,
  Entity,
  JoinColumn,
  OneToOne,
  PrimaryColumn,
  UpdateDateColumn,
} from 'typeorm';
import { v4 as uuidv4 } from 'uuid';
import { Team } from '../../teams/entities/team.entity';

export enum ServiceStatus {
  ACTIVE = 'active',
  DEPRECATED = 'deprecated',
}

@Entity('services')
export class Service {
  @PrimaryColumn({ type: 'varchar', length: 36 })
  id: string;

  @Column({ length: 255, unique: true })
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string | null;

  @Column({
    type: 'enum',
    enum: ServiceStatus,
    default: ServiceStatus.ACTIVE,
  })
  status: ServiceStatus;

  @Column({ name: 'team_id', type: 'varchar', length: 36, nullable: true, unique: true })
  teamId: string | null;

  @OneToOne(() => Team, (team) => team.service, { nullable: true, onDelete: 'SET NULL' })
  @JoinColumn({ name: 'team_id' })
  team: Team | null;

  @Column({ name: 'deprecated_at', type: 'datetime', nullable: true })
  deprecatedAt: Date | null;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  @BeforeInsert()
  generateId() {
    if (!this.id) this.id = uuidv4();
  }
}
