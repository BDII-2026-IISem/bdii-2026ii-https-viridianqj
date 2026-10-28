import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { Aside } from './aside';

describe('Aside', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Aside],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('se crea el menú lateral', () => {
    const fixture = TestBed.createComponent(Aside);
    fixture.detectChanges();
    expect(fixture.componentInstance).toBeTruthy();
  });
});
