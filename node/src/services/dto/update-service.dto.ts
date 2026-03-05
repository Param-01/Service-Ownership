import { IsNotEmpty, IsOptional, IsString, IsUUID, ValidateIf } from 'class-validator';

export class UpdateServiceDto {
  @ValidateIf((o: UpdateServiceDto) => o.name !== undefined)
  @IsString()
  @IsNotEmpty({ message: 'name cannot be empty' })
  name?: string;

  @IsOptional()
  @IsString()
  description?: string | null;

  // null is allowed to unassign the team
  @IsOptional()
  @IsUUID()
  teamId?: string | null;
}
