#!/usr/bin/env python3
"""Browser smoke checks for the generated offline replay (optional local dependency)."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay',type=Path,default=Path('results/raw/visualization/replay.html'))
    parser.add_argument('--output',type=Path,default=Path('results/raw/browser'))
    parser.add_argument('--executable',type=str)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        options={'headless':True}
        if args.executable:options['executable_path']=args.executable
        browser=pw.chromium.launch(**options)
        page=browser.new_page(viewport={'width':960,'height':900})
        errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto(args.replay.resolve().as_uri())
        assert page.locator('[data-config] option').count()==18
        for mode in ('grid','surface','space'):
            page.locator('[data-view]').select_option(mode)
            assert page.locator('[data-plot] > *').count()>10
            page.screenshot(path=str(args.output/f'{mode}_desktop.png'))
        before=page.locator('[data-clock]').inner_text()
        page.locator('[data-next]').click()
        assert page.locator('[data-clock]').inner_text()!=before
        page.locator('[data-back]').click()
        assert page.locator('[data-clock]').inner_text()==before
        page.locator('[data-config]').select_option(label='P=2 · N=8 · B=4 words/clock')
        page.locator('[data-view]').select_option('grid')
        assert page.locator('svg rect').count()==4
        page.locator('[data-config]').select_option(label='P=8 · N=16 · B=4 words/clock')
        page.locator('[data-play]').click();page.wait_for_timeout(350)
        page.locator('[data-play]').click()
        assert page.locator('[data-clock]').inner_text()!=before
        for mode in ('grid','surface','space'):
            page.locator('[data-view]').select_option(mode)
            page.set_viewport_size({'width':360,'height':900})
            page.wait_for_timeout(80)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.screenshot(path=str(args.output/f'{mode}_mobile.png'))
        assert not errors,errors
        browser.close()
    print('PASS: replay configuration, view modes, clock controls, playback, and mobile layout')


if __name__=='__main__':main()
