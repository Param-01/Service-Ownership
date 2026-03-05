import { IsNotEmpty, IsOptional, IsString, ValidateIf } from 'class-validator';

export class UpdateTeamDto {
  // Only validate if name was explicitly provided (not undefined).
  // Sending name: null will fail @IsString(); sending nothing skips validation.
  @ValidateIf((o: UpdateTeamDto) => o.name !== undefined)
  @IsString()
  @IsNotEmpty({ message: 'name cannot be empty' })
  name?: string;

  // null is allowed to clear the description
  @IsOptional()
  @IsString()
  description?: string | null;
}
