"""Render CMS-ready admissions planning copy without evaluating eligibility."""
import html

def e(value):
    return html.escape(str(value), quote=True)

def admission_journey(routes):
    choices = []
    panels = []
    for index, route in enumerate(routes):
        ident = e(route['id'])
        choices.append(f'<a href="{e(route["guide"])}" data-journey-route="{ident}"><span class="journey-choice-number" aria-hidden="true">0{index+1}</span><span class="journey-choice-title">{e(route["title"])}</span><small>{e(route["description"])}</small><span class="arrow" aria-hidden="true">→</span></a>')
        steps = []
        for step_index, step in enumerate(route['steps']):
            action = step['link']
            steps.append(f'<li><span class="journey-step-number" aria-hidden="true">0{step_index+1}</span><div><h4>{e(step["title"])}</h4><p>{e(step["copy"])}</p><a class="text-link" href="{e(action["href"])}">{e(action["label"])}<span class="arrow" aria-hidden="true">→</span></a></div></li>')
        prompts = ''.join(f'<label><input type="checkbox"><span>{e(prompt)}</span></label>' for prompt in route['readiness'])
        panels.append(f'<article class="journey-route" id="journey-{ident}" data-journey-panel="{ident}" aria-labelledby="journey-{ident}-heading"><div class="eyebrow">Your next steps</div><h3 id="journey-{ident}-heading">{e(route["title"])}</h3><p>{e(route["intro"])}</p><ol class="journey-steps">'+''.join(steps)+f'</ol><details class="journey-readiness"><summary>Before you apply<span class="disclosure-icon" aria-hidden="true"></span></summary><div class="readiness-content"><p>Use these prompts to organize your preparation. Your current official admission guidance determines the requirements.</p>{prompts}</div></details></article>')
    return '<div class="admission-journey" data-admission-journey><h2>Find your application pathway</h2><p>Choose a route to explore the preparation ahead. The university can help confirm which applicant category applies to you.</p><nav class="journey-choices" aria-label="Explore application routes">'+''.join(choices)+'</nav><p class="journey-prompt">Select a pathway to see the next steps.</p><p class="journey-status" data-journey-status aria-live="polite" aria-atomic="true"></p><div class="journey-panels">'+''.join(panels)+'</div><p class="journey-help">Not sure where to start? <a href="mailto:iadept@saturn.yzu.edu.tw">Ask the Global Affairs Office</a> or <a href="about.html#visit">contact IBSC</a>.</p></div>'
