(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // Scroll reveal
  const revealed = $$('[data-reveal]');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    revealed.forEach((el) => io.observe(el));
  } else {
    revealed.forEach((el) => el.classList.add('is-in'));
  }

  // Mobile nav
  const toggle = $('[data-nav-toggle]');
  const nav = $('[data-nav]');
  const setNav = (open) => {
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  };
  toggle.addEventListener('click', () => setNav(!nav.classList.contains('is-open')));
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) setNav(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setNav(false); });

  // Header shadow and back-to-top
  const header = $('[data-header]');
  const toTop = $('[data-to-top]');
  const onScroll = () => {
    header.classList.toggle('is-stuck', scrollY > 60);
    toTop.classList.toggle('is-visible', scrollY > 600);
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Active nav link follows the section in view
  const links = $$('.nav > a[href^="#"]');
  const linkFor = (section) => links.find((l) => (l.hash === '#top' ? section.matches('.hero') : `#${section.id}` === l.hash));
  if ('IntersectionObserver' in window) {
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const match = linkFor(entry.target);
        links.forEach((l) => l.classList.toggle('is-active', l === match));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    $$('main > section').forEach((section) => spy.observe(section));
  }

  // Accordions: one panel open at a time, with a matching image
  $$('[data-accordion]').forEach((group) => {
    const items = $$('.acc', group);
    const images = $$('[data-panel-img]', group);
    items.forEach((item, index) => {
      $('.acc__head', item).addEventListener('click', () => {
        items.forEach((other, i) => {
          const open = i === index;
          other.classList.toggle('is-open', open);
          $('.acc__head', other).setAttribute('aria-expanded', String(open));
        });
        images.forEach((img, i) => {
          if (i === index) img.loading = 'eager';
          img.classList.toggle('is-active', i === index);
        });
      });
    });
  });

  // Locations carousel
  $$('[data-carousel]').forEach((carousel) => {
    const track = $('[data-track]', carousel);
    const prev = $('[data-prev]', carousel);
    const next = $('[data-next]', carousel);
    const dots = $('[data-dots]', carousel);
    const slides = [...track.children];

    const offset = (i) => slides[i].offsetLeft - slides[0].offsetLeft;
    const stops = () => {
      const max = track.scrollWidth - track.clientWidth;
      const positions = slides.map((_, i) => offset(i)).filter((x) => x < max - 2);
      positions.push(max);
      return positions;
    };
    const current = () => {
      const list = stops();
      let best = 0;
      list.forEach((x, i) => { if (Math.abs(x - track.scrollLeft) < Math.abs(list[best] - track.scrollLeft)) best = i; });
      return best;
    };
    const goTo = (i) => {
      const list = stops();
      track.scrollTo({ left: list[Math.max(0, Math.min(i, list.length - 1))], behavior: 'smooth' });
    };
    const render = () => {
      const list = stops();
      if (dots.children.length !== list.length) {
        dots.replaceChildren(...list.map((_, i) => {
          const dot = document.createElement('button');
          dot.type = 'button';
          dot.setAttribute('aria-label', `Go to location ${i + 1}`);
          dot.addEventListener('click', () => goTo(i));
          return dot;
        }));
      }
      const at = current();
      [...dots.children].forEach((dot, i) => dot.setAttribute('aria-current', String(i === at)));
      prev.disabled = at === 0;
      next.disabled = at === list.length - 1;
    };

    prev.addEventListener('click', () => goTo(current() - 1));
    next.addEventListener('click', () => goTo(current() + 1));
    track.addEventListener('scroll', render, { passive: true });
    addEventListener('resize', render);
    render();
  });

  // Contact form: validates, then opens a prepared email to grabEAT
  const form = $('[data-contact-form]');
  const status = $('[data-form-status]');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const required = $$('input[required]', form);
    let firstInvalid = null;
    required.forEach((input) => {
      const valid = input.checkValidity();
      input.closest('.field').classList.toggle('is-invalid', !valid);
      input.setAttribute('aria-invalid', String(!valid));
      if (!valid && !firstInvalid) firstInvalid = input;
    });
    if (firstInvalid) {
      status.textContent = 'Please enter a valid email and phone number.';
      status.classList.add('is-error');
      firstInvalid.focus();
      return;
    }
    const data = new FormData(form);
    const name = `${data.get('first')} ${data.get('last')}`.trim();
    const topics = data.getAll('topic');
    const body = [
      `Name: ${name}`,
      `Email: ${data.get('email')}`,
      `Phone: ${data.get('phone')}`,
      `Topics: ${topics.join(', ') || '-'}`,
      `Further communications: ${data.get('optin') ? 'Yes' : 'No'}`,
      '',
      data.get('message'),
    ].join('\n');
    const subject = `grabEAT website enquiry${name ? ` from ${name}` : ''}`;
    status.classList.remove('is-error');
    status.textContent = 'Opening your email app with your message ready to send.';
    location.href = `mailto:post@grabeat.no?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
  form.addEventListener('input', (e) => {
    const field = e.target.closest('.field');
    if (field && field.classList.contains('is-invalid') && e.target.checkValidity()) {
      field.classList.remove('is-invalid');
      e.target.removeAttribute('aria-invalid');
    }
  });

  $('[data-year]').textContent = new Date().getFullYear();
})();
