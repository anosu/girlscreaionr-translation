from update import Updater

if __name__ == '__main__':
    Updater(
        translation_dir='.',
        download_dir='GalTransl/gt_input'
    ).run()
