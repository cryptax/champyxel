champyxel.html: champyxel.pyxapp
	pyxel app2html $<

champyxel.pyxapp: ../pico.py ../pico.pyxres
	cp ../pico.py ../pico.pyxres .
	pyxel package . pico.py
	mv *.pyxapp champyxel.pyxapp
	rm -f pico.py pico.pyxres

clean:
	rm -f pico.py pico.pyxres champyxel.pyxapp
