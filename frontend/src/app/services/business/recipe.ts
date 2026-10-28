import { Injectable } from '@angular/core';

import { RecipeI } from '../../models/business/recipe';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class RecipeService extends BaseApi<RecipeI> {
  protected readonly path = 'recetas';
}
