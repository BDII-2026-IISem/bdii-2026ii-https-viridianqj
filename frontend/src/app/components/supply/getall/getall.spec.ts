import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { Getall } from './getall';

describe('Getall (insumos)', () => {
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Getall],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });

  it('se crea', () => {
    const fixture = TestBed.createComponent(Getall);
    fixture.detectChanges();
    expect(fixture.componentInstance).toBeTruthy();
    http.match(() => true);
  });

  it('carga la lista desde /insumos/', () => {
    const fixture = TestBed.createComponent(Getall);
    fixture.detectChanges();

    const req = http.expectOne((r) => r.url.includes('/insumos'));
    expect(req.request.method).toBe('GET');
    req.flush([]);

    expect(fixture.componentInstance.items().length).toBe(0);
    expect(fixture.componentInstance.loading()).toBe(false);
  });
});
