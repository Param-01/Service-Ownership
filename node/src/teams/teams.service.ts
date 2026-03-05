import { ConflictException, Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Team } from './entities/team.entity';
import { CreateTeamDto } from './dto/create-team.dto';
import { UpdateTeamDto } from './dto/update-team.dto';

@Injectable()
export class TeamsService {
  constructor(
    @InjectRepository(Team)
    private readonly repo: Repository<Team>,
  ) {}

  async create(dto: CreateTeamDto): Promise<Team> {
    const existing = await this.repo.findOneBy({ name: dto.name });
    if (existing) throw new ConflictException('Team name already exists');

    const team = this.repo.create({
      name: dto.name,
      description: dto.description ?? null,
    });
    return this.repo.save(team);
  }

  async update(id: string, dto: UpdateTeamDto): Promise<Team> {
    const team = await this.repo.findOne({ where: { id }, relations: ['service'] });
    if (!team) throw new NotFoundException('Team not found');

    if (dto.name !== undefined) {
      const conflict = await this.repo.findOneBy({ name: dto.name });
      if (conflict && conflict.id !== id) throw new ConflictException('Team name already exists');
      team.name = dto.name;
    }
    if ('description' in dto) {
      team.description = dto.description ?? null;
    }

    return this.repo.save(team);
  }

  async findOneWithService(id: string): Promise<Team> {
    const team = await this.repo.findOne({ where: { id }, relations: ['service'] });
    if (!team) throw new NotFoundException('Team not found');
    return team;
  }
}
